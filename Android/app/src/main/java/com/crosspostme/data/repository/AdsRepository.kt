package com.crosspostme.data.repository

import com.crosspostme.data.api.AdsApiService
import com.crosspostme.data.model.*
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.flow
import javax.inject.Inject
import javax.inject.Singleton

/**
 * Repository for Ads data
 * Following MVVM architecture patterns and backend API structure
 * Handles API calls and error management
 */
@Singleton
class AdsRepository @Inject constructor(
    private val adsApiService: AdsApiService
) {
    
    // Create a new ad
    suspend fun createAd(ad: AdCreate): Result<Ad> {
        return try {
            val response = adsApiService.createAd(ad)
            if (response.isSuccessful && response.body() != null) {
                Result.success(response.body()!!)
            } else {
                Result.failure(Exception("Error creating ad: ${response.message()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    // Get all ads with optional filtering
    fun getAds(status: String? = null, platform: String? = null): Flow<Result<List<Ad>>> = flow {
        try {
            val response = adsApiService.getAds(status, platform)
            if (response.isSuccessful && response.body() != null) {
                emit(Result.success(response.body()!!))
            } else {
                emit(Result.failure(Exception("Error fetching ads: ${response.message()}")))
            }
        } catch (e: Exception) {
            emit(Result.failure(e))
        }
    }
    
    // Get ad by ID
    suspend fun getAd(adId: String): Result<Ad> {
        return try {
            val response = adsApiService.getAd(adId)
            if (response.isSuccessful && response.body() != null) {
                Result.success(response.body()!!)
            } else {
                Result.failure(Exception("Ad not found"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    // Update an ad
    suspend fun updateAd(adId: String, adUpdate: AdUpdate): Result<Ad> {
        return try {
            val response = adsApiService.updateAd(adId, adUpdate)
            if (response.isSuccessful && response.body() != null) {
                Result.success(response.body()!!)
            } else {
                Result.failure(Exception("Error updating ad: ${response.message()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    // Delete an ad
    suspend fun deleteAd(adId: String): Result<Boolean> {
        return try {
            val response = adsApiService.deleteAd(adId)
            if (response.isSuccessful) {
                Result.success(true)
            } else {
                Result.failure(Exception("Error deleting ad: ${response.message()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    // Post ad to platform
    suspend fun postAd(adId: String, platform: String): Result<PostedAd> {
        return try {
            val response = adsApiService.postAd(adId, platform)
            if (response.isSuccessful && response.body() != null) {
                Result.success(response.body()!!)
            } else {
                Result.failure(Exception("Error posting ad: ${response.message()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    // Get dashboard stats
    fun getDashboardStats(): Flow<Result<DashboardStats>> = flow {
        try {
            val response = adsApiService.getDashboardStats()
            if (response.isSuccessful && response.body() != null) {
                emit(Result.success(response.body()!!))
            } else {
                emit(Result.failure(Exception("Error fetching dashboard stats: ${response.message()}")))
            }
        } catch (e: Exception) {
            emit(Result.failure(e))
        }
    }
    
    // Get ad analytics
    fun getAdAnalytics(adId: String, days: Int = 7): Flow<Result<List<AdAnalytics>>> = flow {
        try {
            val response = adsApiService.getAdAnalytics(adId, days)
            if (response.isSuccessful && response.body() != null) {
                emit(Result.success(response.body()!!))
            } else {
                emit(Result.failure(Exception("Error fetching analytics: ${response.message()}")))
            }
        } catch (e: Exception) {
            emit(Result.failure(e))
        }
    }
}